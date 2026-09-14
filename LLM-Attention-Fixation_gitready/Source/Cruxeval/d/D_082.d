import std.math;
import std.typecons;
string f(string a, string b, string c, string d) 
{
    return a.length > 0 ? b : c.length > 0 ? d : "";
}
unittest
{
    alias candidate = f;

    assert(candidate("CJU", "BFS", "WBYDZPVES", "Y") == "BFS");
}
void main(){}
