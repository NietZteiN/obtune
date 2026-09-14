import std.math;
import std.typecons;
import std.string;
import std.ascii;

bool f(string text) 
{
    foreach (c; text)
    {
        if (!isDigit(c))
        {
            return false;
        }
    }
    return !text.empty;
}
unittest
{
    alias candidate = f;

    assert(candidate("99") == true);
}
void main(){}
