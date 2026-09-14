import std.math;
import std.typecons;
string f(string text, long n) 
{
    if (n < 0 || text.length <= n) {
        return text;
    }
    
    string result = text[0 .. n];
    long i = result.length - 1;
    while (i >= 0) {
        if (result[i] != text[i]) {
            break;
        }
        i--;
    }
    
    return text[0 .. i + 1];
}
unittest
{
    alias candidate = f;

    assert(candidate("bR", -1L) == "bR");
}
void main(){}
