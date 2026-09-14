import std.math;
import std.typecons;
import std.algorithm;
import std.array;
import std.string;

string f(string[] names) 
{
    if(names.length == 0)
    {
        return "";
    }
    string smallest = names[0];
    foreach(name; names[1 .. $])
    {
        if(name < smallest)
        {
            smallest = name;
        }
    }
    names = names.filter!(a => a != smallest).array;
    return smallest;
}
unittest
{
    alias candidate = f;

    assert(candidate([]) == "");
}
void main(){}
