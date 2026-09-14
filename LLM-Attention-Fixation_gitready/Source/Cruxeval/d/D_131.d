import std.math;
import std.typecons;
import std.string;

long f(string text) 
{
    long a = text.length;
    long count = 0;
    while (text.length > 0)
    {
        if (text.startsWith('a'))
        {
            count += text.indexOf(' ');
        }
        else
        {
            count += text.indexOf('\n');
        }
        text = text.split('\n')[1..$].join("\n");
    }
    return count;
}
unittest
{
    alias candidate = f;

    assert(candidate("a
kgf
asd
") == 1L);
}
void main(){}
