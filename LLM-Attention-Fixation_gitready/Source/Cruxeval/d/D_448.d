import std.math;
import std.typecons;
bool f(string text, string suffix) 
{
    if (suffix == "")
    {
        suffix = null;
    }
    return text[$-suffix.length .. $] == suffix;
}
unittest
{
    alias candidate = f;

    assert(candidate("uMeGndkGh", "kG") == false);
}
void main(){}
