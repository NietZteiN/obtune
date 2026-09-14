import std.math;
import std.typecons;
import std.string;

string f(string s) 
{
    return s.toUpper;
}
unittest
{
    alias candidate = f;

    assert(candidate("Jaafodsfa SOdofj AoaFjIs  JAFasIdfSa1") == "JAAFODSFA SODOFJ AOAFJIS  JAFASIDFSA1");
}
void main(){}
