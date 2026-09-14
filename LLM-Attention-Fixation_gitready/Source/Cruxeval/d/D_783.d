import std.math;
import std.typecons;
long f(string text, string comparison) 
{
    long length = comparison.length;
    if (length <= text.length) {
        for (long i = 0; i < length; i++) {
            if (comparison[length - i - 1] != text[text.length - i - 1]) {
                return i;
            }
        }
    }
    return length;
}
unittest
{
    alias candidate = f;

    assert(candidate("managed", "") == 0L);
}
void main(){}
