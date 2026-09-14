import std.math;
import std.typecons;
import std.string;
import std.algorithm;

string f(string text, string prefix) 
{
    if (text.startsWith(prefix))
    {
        return text[prefix.length .. $];
    }
    if (text.canFind(prefix))
    {
        return text.replace(prefix, "").strip();
    }
    return text.toUpper();
}
unittest
{
    alias candidate = f;

    assert(candidate("abixaaaily", "al") == "ABIXAAAILY");
}
void main(){}
