import std.algorithm;
import std.array;
import std.string;
import std.typecons;

string f(string text, string old, string newStr) {
    if (old.length > 3) {
        return text;
    }
    if (text.canFind(old) && !text.canFind(' ')) {
        return text.replace(old, newStr.replicate(old.length));
    }
    while (text.canFind(old)) {
        text = text.replace(old, newStr);
    }
    return text;
}

unittest
{
    alias candidate = f;

    assert(candidate("avacado", "va", "-") == "a--cado");
}
void main(){}
