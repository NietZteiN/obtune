import std.math;
import std.typecons;

long f(string numbers) 
{
    int count = 0;
    foreach (char c; numbers) {
        if (c == '3') {
            count++;
        }
    }

    for (int i = 0; i < numbers.length; i++) {
        if (count > 1) {
            return i;
        }
    }
    return -1;
}
unittest
{
    alias candidate = f;

    assert(candidate("23157") == -1L);
}
void main(){}
