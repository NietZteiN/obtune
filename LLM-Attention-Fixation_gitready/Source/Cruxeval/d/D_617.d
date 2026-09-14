import std.math;
import std.typecons;
import std.string;

string f(string text)
{
    foreach (i, c; text)
    {
        if (c > 127)
            return "non ascii";
    }
    return "ascii";
}
unittest
{
    alias candidate = f;

    assert(candidate("<<<<") == "ascii");
}
void main(){}
