import std.math;
import std.typecons;
import std.array;

long[] f(string text) 
{
    char[char] name;
    name['a'] = 'b';
    name['b'] = 'c';
    name['c'] = 'd';
    name['d'] = 'e';
    name['e'] = 'f';

    long[char] occ;
    foreach (ch; text)
    {
        char name_char = name.get(ch, ch);
        occ[name_char] = occ.get(name_char, 0) + 1;
    }
    return occ.values;
}
unittest
{
    alias candidate = f;

    assert(candidate("URW rNB") == [1L, 1L, 1L, 1L, 1L, 1L, 1L]);
}
void main(){}
