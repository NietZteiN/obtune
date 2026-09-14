import std.math;
import std.typecons;
long f(long[] album_sales) 
{
    while (album_sales.length != 1) {
        album_sales ~= album_sales[0]; // append to end
        album_sales = album_sales[1..$]; // remove first element
    }
    return album_sales[0];
}
unittest
{
    alias candidate = f;

    assert(candidate([6L]) == 6L);
}
void main(){}
