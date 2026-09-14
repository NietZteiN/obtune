import std.algorithm;
import std.string;

bool f(string text, string ch) {
    return count(text, ch[0]) % 2 != 0;
}

unittest
{
    alias candidate = f;

    assert(candidate("abababac", "a") == false);
}
void main(){}
