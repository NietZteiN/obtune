import std.math;
import std.typecons;
import std.conv;
import std.ascii;

long f(string letters) 
{
    long count = 0;
    foreach (char l; letters) {
        if (isDigit(l)) {
            count++;
        }
    }
    return count;
}
unittest
{
    alias candidate = f;

    assert(candidate("dp ef1 gh2") == 2L);
}
void main(){}
