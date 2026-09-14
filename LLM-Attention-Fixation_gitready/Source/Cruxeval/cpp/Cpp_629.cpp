#include<assert.h>
#include<bits/stdc++.h>
std::string f(std::string text, std::string dng) {
    if(text.find(dng) == std::string::npos){
        return text;
    }
    if(text.substr(text.length()-dng.length()) == dng){
        return text.substr(0, text.length()-dng.length());
    }
    return text.substr(0, text.length()-1) + f(text.substr(0, text.length()-2), dng);
}
int main() {
    auto candidate = f;
    assert(candidate(("catNG"), ("NG")) == ("cat"));
}
