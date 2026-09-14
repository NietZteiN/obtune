import std.math;
import std.typecons;
import std.ascii;

string f(string s) 
{
    string result;
    foreach (c; s)
    {
        if (isWhite(c))
        {
            result ~= c;
        }
    }
    return result;
}
unittest
{
    alias candidate = f;

    assert(candidate("
giyixjkvu
 rgjuo") == "

 ");
}
void main(){}
