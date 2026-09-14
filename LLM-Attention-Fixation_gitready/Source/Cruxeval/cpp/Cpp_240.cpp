#include<assert.h>
#include<bits/stdc++.h>
std::string f(float float_number) {
    std::stringstream ss;
    ss << float_number;
    std::string number = ss.str();
    int dot = number.find('.');
    if (dot != std::string::npos) {
        if (number.size() - dot < 3) {
            number.append((3 - (number.size() - dot)), '0');
        }
        return number;
    }
    return number + ".00";
}
int main() {
    auto candidate = f;
    assert(candidate((3.121f)) == ("3.121"));
}
