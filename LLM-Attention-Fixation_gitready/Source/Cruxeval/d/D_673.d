import std.math;
import std.typecons;
import std.string;

string f(string string) 
{
    if (string.toUpper == string)
    {
        return toLower(string);
    }
    else if (string.toLower == string)
    {
        return toUpper(string);
    }
    
    return string;
}
unittest
{
    alias candidate = f;

    assert(candidate("cA") == "cA");
}
void main(){}
