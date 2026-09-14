import std.math;
import std.typecons;
import std.string;
import std.algorithm;
import std.array;
import std.ascii;

Tuple!(long, string) f(string text, string lower, string upper) {
    long count = 0;
    string new_text;
    foreach (char c; text) {
        char new_char = c.isDigit ? lower[0] : upper[0];
        if (new_char == 'p' || new_char == 'C') {
            count++;
        }
        new_text ~= new_char;
    }
    return tuple(count, new_text);
}

unittest
{
    alias candidate = f;

    assert(candidate("DSUWeqExTQdCMGpqur", "a", "x") == tuple(0L, "xxxxxxxxxxxxxxxxxx"));
}
void main(){}
