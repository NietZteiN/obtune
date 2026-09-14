import std.algorithm;
import std.array;
import std.string;
import std.conv; // Import std.conv to use the to function

string f(string s, string separator) {
    for (size_t i = 0; i < s.length; i++) {
        if (s[i] == separator[0]) {
            auto new_s = s.dup;
            new_s[i] = '/';
            return new_s.map!(c => c.to!string).join(" ");
        }
    }
    return s; // In case no separator is found, return the original string
}

unittest
{
    alias candidate = f;

    assert(candidate("h grateful k", " ") == "h / g r a t e f u l   k");
}
void main(){}
