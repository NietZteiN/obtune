import std.math;
import std.typecons;
string f(string value) 
{
    auto ls = value;
    ls ~= "NHIB";
    return ls;
}
unittest
{
    alias candidate = f;

    assert(candidate("ruam") == "ruamNHIB");
}
void main(){}
