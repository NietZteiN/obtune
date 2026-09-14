import std.math;
import std.typecons;
import std.array;
import std.string;

string f(string text) 
{
    string result;
    foreach(line; text.split("\n"))
    {
        if (!result.empty)
            result ~= ", ";
        result ~= line;
    }
    return result;
}
unittest
{
    alias candidate = f;

    assert(candidate("BYE
NO
WAY") == "BYE, NO, WAY");
}
void main(){}
