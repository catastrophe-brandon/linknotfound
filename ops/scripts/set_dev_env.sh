#!/bin/bash

# terminal color
color_default="\e[39m"
color_error="\e[31m"
color_ok="\e[32m"
color_header="\e[34m"

# requirements
req_rm="python3-devel* git"
req_pip=""

# default answers
default_dir="$(pwd)"
default_dir_venv="$default_dir/venv"
default_app="Code Seeker"

welcome() {
  clear
  echo "Installer"
  print_header "Installing development environment"
  echo "$default_app"
}

print_header() {
  echo
  echo -e "--$color_header $1 $color_default"
}

print_check() {
  case $1 in
  ok | 0)
    echo -e "[$color_ok v $color_default] $2"
    ;;
  error | 1)
    echo -e "[$color_error x $color_default] $2"
    exit 1
    ;;
  esac
}

check_os() {
  print_header "Check OS compatibility"
  if [ ! -f "/etc/redhat-release" ]; then
    print_check 1 "OS not compatible"
  fi
  print_check 0 "OS compatibility"
}

requirements() {
  print_header "Check requirements ( RPM packages and pip modules )"
  for pkg in "${req_rpm[@]}"; do
    if [ ! $(rpm -qa $pkg) ]; then
      print_check 1 "required package $pkg not found"
    fi
  done
  print_check 0 "required packages"

  # check for pip requirements
  if [ -z ${#req_pip[@]} ]; then
    for pip in "${req_pip[@]}"; do
      if ! pip freeze | grep $pip >/dev/null 2>&1; then
        print_check 1 "required pip $pip not found"
      fi
    done
  fi
  print_check 0 "required pip"

}

question_install_path() {
  echo
  read -p "path to install [$default_dir]: " install_dir
  default_dir="${install_dir:-$default_dir}"
}

question_venv_dir() {
  echo
  read -p "path to create python venv(s) [$default_dir_venv]: " install_dir
  default_dir_venv="${install_dir:-$default_dir_venv}"
}

venv() {
  print_header "Preparing python venv"
  mkdir -p $default_dir_venv

  it_venv="$(find $default_dir -type d -name "seeker")"

  if [ -z "$it_venv" ]; then
    print_check 1 "seeker not found at $default_dir_venv"
  fi

  {
    venv_name="$default_dir_venv"
    mkdir -p $venv_name
    python3 -m venv "$venv_name" >/dev/null 2>&1
    print_check 0 "venv initialized $venv_name"
  } || {
    print_check 1 "venv initialized $venv_name"
  }
  {
    $venv_name/bin/pip install devpi-client >/dev/null 2>&1
    $venv_name/bin/pip install -U pip setuptools setuptools_scm wheel >/dev/null 2>&1
    print_check 0 "installing basic dependencies, wait..."
    $venv_name/bin/pip install -r requirements.txt >/dev/null 2>&1
    print_check 0 "installing pip requirements"
    $venv_name/bin/python3 -m pip install -e . >/dev/null 2>&1
    print_check 0 "installing seeker as --editable"
  } || {
    print_check 1 "venv installing $venv_name"
  }
}

summary() {
  print_header "Summary"
  echo "Complete environment setup $(($end - $start)) seconds"
  echo "projects and venv at $default_dir"
  echo
}

welcome
question_install_path
question_venv_dir
check_os
requirements
start=$(date +'%s')
venv
end=$(date +'%s')
summary
