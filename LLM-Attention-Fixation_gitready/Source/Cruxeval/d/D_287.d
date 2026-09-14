import std.math;
import std.typecons;
import std.string;

string f(string name) 
{
    if (name.toLower == name)
    {
        name = name.toUpper;
    }
    else
    {
        name = name.toLower;
    }
    return name;
}
unittest
{
    alias candidate = f;

    assert(candidate("Pinneaple") == "pinneaple");
}
void main(){}
