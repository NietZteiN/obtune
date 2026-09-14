import std.algorithm;
import std.array;
import std.string;

string f(string text) {
    char[] ls = text.dup;
    foreach_reverse (x; 0 .. ls.length) {
        if (ls.length <= 1) break;
        if (!"zyxwvutsrqponmlkjihgfedcba".canFind(ls[x])) ls = ls.remove(x);
    }
    return ls.idup;
}

unittest
{
    alias candidate = f;

    assert(candidate("qq") == "qq");
}
void main(){}
