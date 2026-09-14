import std.math;
import std.typecons;
import std.conv;
import std.exception;

long f(string s) 
{
    long pos = s.length;
    while (pos != 0) {
        pos--;
        if (s[pos] == 'e') {
            return pos;
        }
    }
    throw new Exception("Nuk");
}
unittest
{
    alias candidate = f;

    assert(candidate("eeuseeeoehasa") == 8L);
}
void main(){}
