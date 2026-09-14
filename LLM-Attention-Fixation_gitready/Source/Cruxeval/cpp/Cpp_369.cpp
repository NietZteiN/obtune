#include<assert.h>
#include<bits/stdc++.h>
std::string f(std::string var) {
    if(std::all_of(var.begin(), var.end(), ::isdigit)) {
        return "int";
    } else if(std::count(var.begin(), var.end(), '.') == 1 && std::all_of(var.begin(), var.end(), [](char c) { return ::isdigit(c) || c == '.'; })) {
        return "float";
    } else if(std::count(var.begin(), var.end(), ' ') == var.length() - 1) {
        return "str";
    } else if(var.length() == 1) {
        return "char";
    } else {
        return "tuple";
    }
}
int main() {
    auto candidate = f;
    assert(candidate((" 99 777")) == ("tuple"));
}
