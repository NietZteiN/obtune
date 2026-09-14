import std.math;
import std.typecons;
import std.algorithm;
import std.array;
import std.string;

string f(string address) 
{
    size_t suffix_start = address.indexOf('@') + 1;
    if (count(address[suffix_start .. $], '.') > 1) {
        auto parts = address.splitter('@').array[1].splitter('.').array;
        address = address[0 .. suffix_start] ~ parts[0] ~ "." ~ parts[1 .. $].join(".");
    }
    return address;
}
unittest
{
    alias candidate = f;

    assert(candidate("minimc@minimc.io") == "minimc@minimc.io");
}
void main(){}
