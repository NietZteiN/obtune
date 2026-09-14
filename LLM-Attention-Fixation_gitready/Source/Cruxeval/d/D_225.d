import std.math;
import std.typecons;
import std.ascii;

bool f(string text) 
{
    foreach (char c; text)
    {
        if (!isLower(c))
        {
            return false;
        }
    }
    return true;
}
unittest
{
    alias candidate = f;

    assert(candidate("54882") == false);
}
void main(){}
