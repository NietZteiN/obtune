import std.math;
import std.typecons;
string f(string text, string pref) 
{
    size_t length = pref.length;
    if (pref == text[0 .. length]) {
        return text[length .. $];
    }
    return text;
}
unittest
{
    alias candidate = f;

    assert(candidate("kumwwfv", "k") == "umwwfv");
}
void main(){}
