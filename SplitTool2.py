import arcpy
arcpy.env.overwriteOutput = True


def create_spaced_lines(rectangle_fc, output_fc, line_count, direction="horizontal"):

    # Check the direction input
    if direction not in ["horizontal", "vertical"]:
        arcpy.AddError("The 'direction' parameter must be either 'horizontal' or 'vertical'.")
        return

    # Get the vertices of the rectangle
    where_clause = f"OBJECTID = {rectangle_id}"
    with arcpy.da.SearchCursor(rectangle_fc, ["SHAPE@"], where_clause=where_clause) as cursor:
        for row in cursor:
            vertices = [pt for pt in row[0].getPart(0)]
            break
        else:
            arcpy.AddError(f"No rectangle found with ID {rectangle_id}.")
            return

    # Calculate side lengths
    side1_length = ((vertices[0].X - vertices[1].X) ** 2 + (vertices[0].Y - vertices[1].Y) ** 2) ** 0.5
    side2_length = ((vertices[1].X - vertices[2].X) ** 2 + (vertices[1].Y - vertices[2].Y) ** 2) ** 0.5

    if direction == "horizontal":
        if side1_length > side2_length:
            start_vertices = [vertices[0], vertices[1]]
            end_vertices = [vertices[3], vertices[2]]
        else:
            start_vertices = [vertices[1], vertices[2]]
            end_vertices = [vertices[0], vertices[3]]
    else:  # vertical
        if side1_length > side2_length:
            start_vertices = [vertices[1], vertices[2]]
            end_vertices = [vertices[0], vertices[3]]
        else:
            start_vertices = [vertices[0], vertices[1]]
            end_vertices = [vertices[3], vertices[2]]

    # Generate the lines
    line_points = []
    for i in range(line_count + 1):
        fraction = i / float(line_count)

        start_point_x = start_vertices[0].X + fraction * (start_vertices[1].X - start_vertices[0].X)
        start_point_y = start_vertices[0].Y + fraction * (start_vertices[1].Y - start_vertices[0].Y)

        end_point_x = end_vertices[0].X + fraction * (end_vertices[1].X - end_vertices[0].X)
        end_point_y = end_vertices[0].Y + fraction * (end_vertices[1].Y - end_vertices[0].Y)

        line_points.append([(start_point_x, start_point_y), (end_point_x, end_point_y)])

    # Write the lines to the output feature class
    arcpy.CreateFeatureclass_management(arcpy.env.workspace, output_fc, "POLYLINE", spatial_reference=rectangle_fc)
    with arcpy.da.InsertCursor(output_fc, ["SHAPE@"]) as cursor:
        for points in line_points:
            cursor.insertRow([arcpy.Polyline(arcpy.Array([arcpy.Point(*pt) for pt in points]))])


def add_to_map(output_fc):

    aprx = arcpy.mp.ArcGISProject("CURRENT")
    active_map = aprx.activeMap
    if arcpy.Exists(output_fc):
        output_full_path = arcpy.env.workspace + "\\" + output_fc
        active_map.addDataFromPath(output_full_path)
    else:
        arcpy.AddError(f"Unable to add {output_fc} to the map. Ensure it was created successfully.")


if __name__ == '__main__':
    rectangle_fc = arcpy.GetParameterAsText(0)
    rectangle_id = int(arcpy.GetParameterAsText(1))
    output_fc = arcpy.GetParameterAsText(2)
    line_count = int(arcpy.GetParameterAsText(3))
    direction = arcpy.GetParameterAsText(4)

    create_spaced_lines(rectangle_fc, output_fc, line_count, direction)

    add_to_map(output_fc)