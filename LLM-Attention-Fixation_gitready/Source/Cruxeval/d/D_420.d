import std.math;
import std.typecons;
import std.ascii;

bool f(string text) 
{
    try {
        foreach (char c; text) {
            if (!isAlpha(c)) {
                return false;
            }
        }
        return true;
    } catch (Throwable) {
        return false;
    }
}
unittest
{
    alias candidate = f;

    assert(candidate("x") == true);
}
void main(){}
