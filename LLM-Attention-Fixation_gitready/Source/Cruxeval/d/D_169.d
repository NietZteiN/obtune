import std.math;
import std.typecons;
import std.string;
import std.conv : to;

string f(string text) {
    auto ls = text.dup;
    int total = cast(int)((text.length - 1) * 2);
    for (int i = 1; i <= total; ++i) {
        if (i % 2 != 0) {
            ls ~= "+";
        } else {
            ls = "+" ~ ls;
        }
    }
    return cast(string)ls;
}

unittest
{
    alias candidate = f;

    assert(candidate("taole") == "++++taole++++");
}
void main(){}
