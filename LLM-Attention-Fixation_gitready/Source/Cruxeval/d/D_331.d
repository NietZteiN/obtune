import std.math;
import std.typecons;
import std.string;
long f(string strand, string zmnc) 
{
    long poz = strand.indexOf(zmnc);
    while (poz != -1) {
        strand = strand[poz + 1 .. $];
        poz = strand.indexOf(zmnc);
    }
    return strand.lastIndexOf(zmnc);
}
unittest
{
    alias candidate = f;

    assert(candidate("", "abc") == -1L);
}
void main(){}
