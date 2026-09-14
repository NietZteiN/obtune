import std.math;
import std.typecons;
import std.algorithm;

string f(string prefix, string text) 
{
    if (text.startsWith(prefix)) {
        return text;
    } else {
        return prefix ~ text;
    }
}
unittest
{
    alias candidate = f;

    assert(candidate("mjs", "mjqwmjsqjwisojqwiso") == "mjsmjqwmjsqjwisojqwiso");
}
void main(){}
