#include<assert.h>
#include<bits/stdc++.h>
std::string f(std::string doc) {
    for(char x : doc){
        if(std::isalpha(x)){
            return std::string(1, std::toupper(x));
        }
    }
    return "-";
}
int main() {
    auto candidate = f;
    assert(candidate(("raruwa")) == ("R"));
}
