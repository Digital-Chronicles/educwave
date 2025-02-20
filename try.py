{% for mark in student_results %}
                    <tr>
                        <td>{{ mark.student.first_name }} {{ mark.student.last_name }}</td>
                        <td>{{ mark.subject.name }}</td>
                        <td>{{ mark.term.term_name }}</td>
                        <td>{{ mark.marks }}</td>
                        <td>{{ mark.teacher.first_name }} {{ mark.teacher.last_name }}</td>
                        <td>
                            <a href="#" class="btn btn-warning btn-sm">Edit</a>
                            <a href="#" class="btn btn-danger btn-sm">Delete</a>
                        </td>
                    </tr>
                    {% endfor %}