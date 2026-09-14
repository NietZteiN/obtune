import std.math;
import std.typecons;
import std.string;

bool f(string text, string pref) 
{
    if (pref[0] == '[' && pref[pref.length - 1] == ']') {
        return text.startsWith(pref[1 .. $ - 1]);
    } else {
        return text.startsWith(pref);
    }
}
unittest
{
    alias candidate = f;

    assert(candidate("Hello World", "W") == false);
}
void main(){}
