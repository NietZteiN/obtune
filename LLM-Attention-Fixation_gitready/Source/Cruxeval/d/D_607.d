import std.math;
import std.typecons;
import std.algorithm;

bool f(string text) 
{
    foreach (i; ['.', '!', '?']) {
        if (text.endsWith(i)) {
            return true;
        }
    }
    return false;
}
unittest
{
    alias candidate = f;

    assert(candidate(". C.") == true);
}
void main(){}
