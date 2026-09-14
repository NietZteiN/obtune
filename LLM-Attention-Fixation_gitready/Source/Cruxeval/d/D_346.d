import std.stdio;
import std.string;
import std.algorithm;
import std.array;

bool f(string filename) {
    string suffix = filename.split('.')[$ - 1];
    string f2 = filename ~ suffix.dup.reverse().idup;
    return f2.endsWith(suffix);
}

unittest
{
    alias candidate = f;

    assert(candidate("docs.doc") == false);
}
void main(){}
