#include<assert.h>
#include<bits/stdc++.h>
std::string f(std::string replace, std::string text, std::string hide) {
    while (text.find(hide) != std::string::npos) {
        replace += "ax";
        text.replace(text.find(hide), hide.length(), replace);
    }
    return text;
}
int main() {
    auto candidate = f;
    assert(candidate(("###"), ("ph>t#A#BiEcDefW#ON#iiNCU"), (".")) == ("ph>t#A#BiEcDefW#ON#iiNCU"));
}
