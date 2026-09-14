#include<assert.h>
#include<bits/stdc++.h>
std::string f(std::string s) {
    std::transform(s.begin(), s.end(), s.begin(), ::toupper);
    return s;
}
int main() {
    auto candidate = f;
    assert(candidate(("Jaafodsfa SOdofj AoaFjIs  JAFasIdfSa1")) == ("JAAFODSFA SODOFJ AOAFJIS  JAFASIDFSA1"));
}
