import std.math;
import std.typecons;
import std.string;

long f(string text, string substr, long occ) {
    long n = 0;
    while (true) {
        long i = text.lastIndexOf(substr);
        if (i == -1) {
            break;
        } else if (n == occ) {
            return i;
        } else {
            n += 1;
            text = text[0 .. i];
        }
    }
    return -1;
}

unittest
{
    alias candidate = f;

    assert(candidate("zjegiymjc", "j", 2L) == -1L);
}
void main(){}
