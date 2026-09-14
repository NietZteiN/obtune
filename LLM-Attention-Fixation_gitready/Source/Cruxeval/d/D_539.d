import std.math;
import std.typecons;
import std.algorithm;
import std.array;
import std.typecons;

alias string_array = string[];

string_array f(string[] array) 
{
    auto array_copy = array[];
    auto ptr = array_copy.ptr;
    while (true)
    {
        array_copy ~= "_";
        if (array_copy.ptr != ptr)
        {
            array_copy[$-1] = "";
            break;
        }
    }
    return array_copy;
}
unittest
{
    alias candidate = f;

    assert(candidate([]) == [""]);
}
void main(){}
