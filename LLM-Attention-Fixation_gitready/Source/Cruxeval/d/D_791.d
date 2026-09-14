import std.math;
import std.typecons;
import std.conv;
import std.string;

string f(long integer, long n) {
    long i = 1;
    string text = to!string(integer);
    while (i + text.length < n) {
        i += text.length;
    }
    return text.rightJustify(i + text.length, '0');
}

unittest
{
    alias candidate = f;

    assert(candidate(8999L, 2L) == "08999");
}
void main(){}
