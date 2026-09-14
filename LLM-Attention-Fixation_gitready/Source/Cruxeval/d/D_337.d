import std.algorithm : map, filter;
import std.ascii : isDigit, isLower, isUpper;
import std.string : toUpper, toLower;

string f(string txt) 
{
    string result = "";
    foreach (c; txt)
    {
        if (isDigit(c)) continue;
        if (isLower(c)) result ~= toUpper(c);
        else if (isUpper(c)) result ~= toLower(c);
    }
    return result;
}

unittest
{
    alias candidate = f;

    assert(candidate("5ll6") == "LL");
}
void main(){}
