import std.math;
import std.typecons;
import std.ascii;
import std.range;
import std.conv;

Tuple!(string, long) f(string s) 
{
    long count = 0;
    string digits = "";
    foreach (c; s) {
        if (c.isDigit) {
            count++;
            digits ~= c;
        }
    }
    return tuple(digits, count);
}
unittest
{
    alias candidate = f;

    assert(candidate("qwfasgahh329kn12a23") == tuple("3291223", 7L));
}
void main(){}
