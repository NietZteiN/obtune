import std.math;
import std.typecons;
import std.string;

string f(string s, long amount) 
{
    string zs = "";
    for (int i = 0; i < amount - s.length; i++)
        zs ~= "z";
    return zs ~ s;
}
unittest
{
    alias candidate = f;

    assert(candidate("abc", 8L) == "zzzzzabc");
}
void main(){}
