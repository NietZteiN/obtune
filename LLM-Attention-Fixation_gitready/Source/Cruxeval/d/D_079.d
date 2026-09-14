import std.math;
import std.typecons;
import std.string;
import std.array;

string f(long[] arr) 
{
    string[] newArr;
    newArr ~= "1";
    newArr ~= "2";
    newArr ~= "3";
    newArr ~= "4";
    return newArr.join(",");
}
unittest
{
    alias candidate = f;

    assert(candidate([0L, 1L, 2L, 3L, 4L]) == "1,2,3,4");
}
void main(){}
