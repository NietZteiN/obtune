#include<assert.h>
#include<bits/stdc++.h>
union Union_std_string_bool{
    std::string f0;
    bool f1;    Union_std_string_bool(std::string _f0) : f0(_f0) {}
    Union_std_string_bool(bool _f1) : f1(_f1) {}
    ~Union_std_string_bool() {}
    bool operator==(std::string f) {
        return f0 == f ;
    }    bool operator==(bool f) {
        return f1 == f ;
    }
};
Union_std_string_bool f(long length, std::string text) {
    if (text.length() == length) {
        std::string reversed_text = text;
        std::reverse(reversed_text.begin(), reversed_text.end());
        return Union_std_string_bool(reversed_text);
    }
    return Union_std_string_bool(false);
}
int main() {
    auto candidate = f;
    assert(candidate((-5), ("G5ogb6f,c7e.EMm")) == false);
}
