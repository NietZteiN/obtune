import std.math;
import std.typecons;
long[] f(long[] list_x) 
{
    auto item_count = list_x.length;
    long[] new_list;
    foreach (_; 0 .. item_count) {
        new_list ~= list_x[$ - 1];
        list_x = list_x[0 .. $ - 1];
    }
    return new_list;
}
unittest
{
    alias candidate = f;

    assert(candidate([5L, 8L, 6L, 8L, 4L]) == [4L, 8L, 6L, 8L, 5L]);
}
void main(){}
